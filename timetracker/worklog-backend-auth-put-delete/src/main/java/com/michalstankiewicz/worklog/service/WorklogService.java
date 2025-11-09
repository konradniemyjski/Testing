package com.michalstankiewicz.worklog.service;

import com.michalstankiewicz.worklog.dto.WorklogDto;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.model.Worklog;
import com.michalstankiewicz.worklog.repository.UserRepository;
import com.michalstankiewicz.worklog.repository.WorklogRepository;
// TODO: jak tylko pokażesz Account i AccountRepository, to to odkomentujemy:
// import com.michalstankiewicz.worklog.model.Account;
// import com.michalstankiewicz.worklog.repository.AccountRepository;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class WorklogService {

    private final WorklogRepository worklogRepository;
    private final UserRepository userRepository;
    // private final AccountRepository accountRepository;

    public WorklogService(
            WorklogRepository worklogRepository,
            UserRepository userRepository
            // , AccountRepository accountRepository
    ) {
        this.worklogRepository = worklogRepository;
        this.userRepository = userRepository;
        // this.accountRepository = accountRepository;
    }

    /* ============================================================
       1. MAPOWANIE "kto jest zalogowany" -> który User w bazie
       ============================================================ */

    /**
     * Zwraca ID użytkownika (tabela User) powiązanego z kontem o danej nazwie (username z JWT).
     *
     * Na razie zwraca null -> wtedy zwykły user dostaje 403 zamiast cudzych danych.
     * Jak tylko pokażesz mi encje Account i User, uzupełnimy to.
     */
    public Long resolveUserIdByUsername(String username) {
        // PRZYKŁAD docelowy:
        //
        // return accountRepository.findByUsername(username)
        //     .map(acc -> {
        //         User u = acc.getUser(); // jeśli Account ma pole user
        //         return (u != null ? u.getId() : null);
        //     })
        //     .orElse(null);
        //
        return null;
    }

    /**
     * Sprawdza czy zalogowany użytkownik (callerUsername) jest właścicielem wpisu (userId wpisu).
     */
    private boolean isOwner(Long worklogUserId, String callerUsername) {
        Long callerUserId = resolveUserIdByUsername(callerUsername);
        return callerUserId != null && callerUserId.equals(worklogUserId);
    }

    /* ============================================================
       2. PUBLICZNE METODY UŻYWANE PRZEZ KONTROLER Z OCHRONĄ
       ============================================================ */

    /**
     * ADMIN: może dostać wszystkie (logika w kontrolerze).
     * USER:  kontroler i tak woła getWorklogsByUserId() tylko z jego ID.
     */
    @Transactional(readOnly = true)
    public List<WorklogDto> getAllWorklogs() {
        return worklogRepository.findAll()
                .stream()
                .map(this::convertToDto)
                .toList();
    }

    /**
     * Zwróć wpisy konkretnego userId.
     * (dla admina: dowolne; dla usera: to już przefiltrował kontroler)
     */
    @Transactional(readOnly = true)
    public List<WorklogDto> getWorklogsByUserId(Long userId) {
        return worklogRepository.findByUserId(userId)
                .stream()
                .map(this::convertToDto)
                .toList();
    }

    /**
     * Dla eksportu admina – wszystkie encje.
     */
    @Transactional(readOnly = true)
    public List<Worklog> getAllWorklogEntities() {
        return worklogRepository.findAll();
    }

    /**
     * Dla eksportu zwykłego usera – tylko jego encje.
     */
    @Transactional(readOnly = true)
    public List<Worklog> getWorklogEntitiesByUserId(Long userId) {
        return worklogRepository.findByUserId(userId);
    }

    /**
     * Pobierz pojedynczy wpis BEZ kontroli dostępu (czysta logika stara).
     * To było wcześniej Twoje getWorklogById.
     */
    @Transactional(readOnly = true)
    public Optional<WorklogDto> getWorklogByIdRaw(Long id) {
        return worklogRepository.findById(id).map(this::convertToDto);
    }

    // === KOMPATYBILNOŚĆ Z ISTNIEJĄCYMI TESTAMI (WorklogServiceTest) ===
    // stare testy wywołują worklogService.getWorklogById(id)
    // więc dajemy wrapper, żeby Maven nie krzyczał
    @Transactional(readOnly = true)
    public Optional<WorklogDto> getWorklogById(Long id) {
        return getWorklogByIdRaw(id);
    }

    /**
     * Pobierz pojedynczy wpis Z KONTROLĄ DOSTĘPU.
     *
     * ADMIN -> dowolny wpis.
     * USER  -> tylko własny wpis.
     */
    @Transactional(readOnly = true)
    public Optional<WorklogDto> getWorklogByIdSecure(
            Long id,
            String callerUsername,
            boolean isAdmin
    ) {
        Optional<Worklog> opt = worklogRepository.findById(id);
        if (opt.isEmpty()) return Optional.empty();

        Worklog wl = opt.get();
        Long wlUserId = wl.getUser() != null ? wl.getUser().getId() : null;

        if (isAdmin || isOwner(wlUserId, callerUsername)) {
            return Optional.of(convertToDto(wl));
        } else {
            return Optional.empty();
        }
    }

    /**
     * Tworzenie wpisu:
     * - ADMIN: może dodać wpis komu chce (dto.userId zostaje jak jest)
     * - USER:  ignorujemy dto.userId i nadpisujemy jego własnym userId
     */
    @Transactional
    public WorklogDto createWorklogSecure(
            WorklogDto worklogDto,
            String callerUsername,
            boolean isAdmin
    ) {
        if (!isAdmin) {
            Long myUserId = resolveUserIdByUsername(callerUsername);
            if (myUserId == null) {
                throw new SecurityException("Brak powiązania konta z użytkownikiem");
            }
            worklogDto.setUserId(myUserId);
        }
        return createWorklog(worklogDto);
    }

    /**
     * Aktualizacja wpisu:
     * - ADMIN: może edytować dowolny wpis
     * - USER:  tylko swój + nie może przepisać wpisu na kogoś innego
     */
    @Transactional
    public Optional<WorklogDto> updateWorklogSecure(
            Long id,
            WorklogDto worklogDto,
            String callerUsername,
            boolean isAdmin
    ) {
        Optional<Worklog> optWl = worklogRepository.findById(id);
        if (optWl.isEmpty()) {
            return Optional.empty();
        }

        Worklog existing = optWl.get();
        Long wlUserId = existing.getUser() != null ? existing.getUser().getId() : null;

        if (!isAdmin && !isOwner(wlUserId, callerUsername)) {
            throw new SecurityException("Brak uprawnień do edycji tego wpisu");
        }

        if (!isAdmin) {
            Long myUserId = resolveUserIdByUsername(callerUsername);
            if (myUserId == null) {
                throw new SecurityException("Brak powiązania konta z użytkownikiem");
            }
            worklogDto.setUserId(myUserId);
        }

        return updateWorklog(id, worklogDto);
    }

    /**
     * Kasowanie wpisu:
     * - ADMIN: może wszystko
     * - USER:  tylko własny wpis
     */
    @Transactional
    public boolean deleteWorklogSecure(
            Long id,
            String callerUsername,
            boolean isAdmin
    ) {
        Optional<Worklog> optWl = worklogRepository.findById(id);
        if (optWl.isEmpty()) {
            return false;
        }

        Worklog wl = optWl.get();
        Long wlUserId = wl.getUser() != null ? wl.getUser().getId() : null;

        if (!isAdmin && !isOwner(wlUserId, callerUsername)) {
            return false;
        }

        return deleteWorklog(id);
    }

    /* ============================================================
       3. BIZNESOWE METODY BAZOWE (bez logiki dostępu)
       ============================================================ */

    @Transactional
    public WorklogDto createWorklog(WorklogDto worklogDto) {
        User user = userRepository.findById(worklogDto.getUserId())
                .orElseThrow(() -> new IllegalArgumentException("Invalid user ID: " + worklogDto.getUserId()));

        Worklog worklog = convertToEntity(worklogDto, user);
        Worklog savedWorklog = worklogRepository.save(worklog);
        return convertToDto(savedWorklog);
    }

    @Transactional
    public Optional<WorklogDto> updateWorklog(Long id, WorklogDto worklogDto) {
        return worklogRepository.findById(id)
                .map(existingWorklog -> {
                    User user = userRepository.findById(worklogDto.getUserId())
                            .orElseThrow(() -> new IllegalArgumentException("Invalid user ID: " + worklogDto.getUserId()));

                    existingWorklog.setWorkDate(worklogDto.getWorkDate());
                    existingWorklog.setUser(user);
                    existingWorklog.setTimeSpent(worklogDto.getTimeSpent());
                    existingWorklog.setMealsOrdered(worklogDto.getMealsOrdered());
                    existingWorklog.setNightsSpent(worklogDto.getNightsSpent());

                    Worklog updatedWorklog = worklogRepository.save(existingWorklog);
                    return convertToDto(updatedWorklog);
                });
    }

    @Transactional
    public boolean deleteWorklog(Long id) {
        if (worklogRepository.existsById(id)) {
            worklogRepository.deleteById(id);
            return true;
        }
        return false;
    }

    /* ============================================================
       4. MAPOWANIA DTO <-> ENTITY
       ============================================================ */

    private WorklogDto convertToDto(Worklog worklog) {
        return new WorklogDto(
                worklog.getId(),
                worklog.getWorkDate(),
                worklog.getUser() != null ? worklog.getUser().getId() : null,
                worklog.getUser() != null ? worklog.getUser().getName() : null,
                worklog.getUser() != null ? worklog.getUser().getSurname() : null,
                worklog.getTimeSpent(),
                worklog.getMealsOrdered(),
                worklog.getNightsSpent()
        );
    }

    private Worklog convertToEntity(WorklogDto worklogDto, User user) {
        Worklog worklog = new Worklog();
        // ID nadaje baza
        worklog.setWorkDate(worklogDto.getWorkDate());
        worklog.setUser(user);
        worklog.setTimeSpent(worklogDto.getTimeSpent());
        worklog.setMealsOrdered(worklogDto.getMealsOrdered());
        worklog.setNightsSpent(worklogDto.getNightsSpent());
        return worklog;
    }
}
