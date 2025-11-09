package com.michalstankiewicz.worklog.controller;

import com.michalstankiewicz.worklog.dto.WorklogDto;
import com.michalstankiewicz.worklog.model.Worklog;
import com.michalstankiewicz.worklog.service.WorklogService;
import com.michalstankiewicz.worklog.util.ExcelExporter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/worklogs")
@CrossOrigin(origins = "*") // Allow requests from Angular dev server
public class WorklogController {

    @Autowired
    private WorklogService worklogService;

    /**
     * LISTA WPISÓW
     *
     * Zasada:
     * - ADMIN:
     *      /api/worklogs           -> wszystkie wpisy
     *      /api/worklogs?userId=X  -> tylko wpisy usera X
     *
     * - ZWYKŁY USER:
     *      ignorujemy param userId i zwracamy tylko jego własne wpisy
     */
    @GetMapping
    public ResponseEntity<List<WorklogDto>> getAllWorklogs(
            @RequestParam(required = false) Long userId,
            Authentication authentication
    ) {
        String callerUsername = authentication.getName();

        boolean isAdmin = authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        if (isAdmin) {
            // admin może wszystko, jak poda userId to filtrujemy
            if (userId != null) {
                return ResponseEntity.ok(worklogService.getWorklogsByUserId(userId));
            } else {
                return ResponseEntity.ok(worklogService.getAllWorklogs());
            }
        } else {
            // zwykły user - nie może podejrzeć cudzych wpisów
            Long myUserId = worklogService.resolveUserIdByUsername(callerUsername);

            if (myUserId == null) {
                // nie umiemy powiązać konta z pracownikiem -> lepiej nic nie pokazać niż wyciek
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }

            return ResponseEntity.ok(worklogService.getWorklogsByUserId(myUserId));
        }
    }

    /**
     * POJEDYNCZY WPIS
     *
     * ADMIN może pobrać dowolny wpis.
     * USER może pobrać tylko swój własny (sprawdzamy w serwisie).
     */
    @GetMapping("/{id}")
    public ResponseEntity<WorklogDto> getWorklogById(
            @PathVariable Long id,
            Authentication authentication
    ) {
        String callerUsername = authentication.getName();
        boolean isAdmin = authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        return worklogService.getWorklogByIdSecure(id, callerUsername, isAdmin)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.status(HttpStatus.FORBIDDEN).build());
    }

    /**
     * TWORZENIE NOWEGO WPISU
     *
     * ADMIN => może zrobić wpis dla dowolnego userId.
     * USER  => może dodać wpis TYLKO dla siebie, nawet jeśli w body poda cudze userId,
     *          to i tak wymusimy jego własne userId.
     */
    @PostMapping
    public ResponseEntity<?> createWorklog(
            @RequestBody WorklogDto worklogDto,
            Authentication authentication
    ) {
        String callerUsername = authentication.getName();
        boolean isAdmin = authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        try {
            WorklogDto createdWorklog = worklogService.createWorklogSecure(worklogDto, callerUsername, isAdmin);
            return new ResponseEntity<>(createdWorklog, HttpStatus.CREATED);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (SecurityException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Brak uprawnień");
        }
    }

    /**
     * AKTUALIZACJA WPISU
     *
     * ADMIN => może edytować dowolny wpis.
     * USER  => tylko swój wpis.
     */
    @PutMapping("/{id}")
    public ResponseEntity<?> updateWorklog(
            @PathVariable Long id,
            @RequestBody WorklogDto worklogDto,
            Authentication authentication
    ) {
        String callerUsername = authentication.getName();
        boolean isAdmin = authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        try {
            return worklogService.updateWorklogSecure(id, worklogDto, callerUsername, isAdmin)
                    .map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (SecurityException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Brak uprawnień");
        }
    }

    /**
     * USUWANIE WPISU
     *
     * ADMIN => może usunąć dowolny wpis.
     * USER  => tylko swój wpis.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteWorklog(
            @PathVariable Long id,
            Authentication authentication
    ) {
        String callerUsername = authentication.getName();
        boolean isAdmin = authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        boolean deleted = worklogService.deleteWorklogSecure(id, callerUsername, isAdmin);

        if (deleted) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }

    /**
     * EXPORT XLS
     * Tu robimy tak samo jak w liście:
     *  - admin: cały Excel
     *  - user: tylko jego wpisy
     */
    @GetMapping("/export/xls")
    public ResponseEntity<InputStreamResource> exportWorklogsToExcel(
            Authentication authentication
    ) {
        String callerUsername = authentication.getName();
        boolean isAdmin = authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        try {
            List<Worklog> worklogs;
            if (isAdmin) {
                worklogs = worklogService.getAllWorklogEntities();
            } else {
                Long myUserId = worklogService.resolveUserIdByUsername(callerUsername);
                if (myUserId == null) {
                    return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
                }
                worklogs = worklogService.getWorklogEntitiesByUserId(myUserId);
            }

            ByteArrayInputStream in = ExcelExporter.worklogsToExcel(worklogs);

            HttpHeaders headers = new HttpHeaders();
            headers.add("Content-Disposition", "attachment; filename=worklogs.xlsx");

            return ResponseEntity
                    .ok()
                    .headers(headers)
                    .contentType(MediaType.parseMediaType(
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ))
                    .body(new InputStreamResource(in));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
