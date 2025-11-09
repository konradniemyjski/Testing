package com.michalstankiewicz.worklog.service;

import com.michalstankiewicz.worklog.dto.WorklogDto;
import com.michalstankiewicz.worklog.model.Account;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.model.Worklog;
import com.michalstankiewicz.worklog.repository.AccountRepository;
import com.michalstankiewicz.worklog.repository.UserRepository;
import com.michalstankiewicz.worklog.repository.WorklogRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class WorklogServiceTest {

    @Mock
    private WorklogRepository worklogRepository;
    @Mock
    private UserRepository userRepository;
    @Mock
    private AccountRepository accountRepository;

    @InjectMocks
    private WorklogService worklogService;

    private User user;
    private Worklog worklog;
    private Account account;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        user = new User(1L, "Jan", "Kowalski", null, new ArrayList<>());
        worklog = new Worklog(1L, LocalDate.now(), user, BigDecimal.valueOf(8.5), 2, 1);
        account = Account.builder().id(5L).username("jan").password("pwd").role("ROLE_USER").user(user).build();
    }

    @Test
    void getAllWorklogs_returnsListOfDtos() {
        when(worklogRepository.findAll()).thenReturn(List.of(worklog));

        List<WorklogDto> result = worklogService.getAllWorklogs();

        assertEquals(1, result.size());
        assertEquals("Jan", result.get(0).getUserName());
        assertEquals(BigDecimal.valueOf(8.5), result.get(0).getTimeSpent());
    }

    @Test
    void getWorklogById_existingId_returnsDto() {
        when(worklogRepository.findById(1L)).thenReturn(Optional.of(worklog));

        Optional<WorklogDto> result = worklogService.getWorklogById(1L);

        assertTrue(result.isPresent());
        assertEquals(2, result.get().getMealsOrdered());
    }

    @Test
    void getWorklogsByUserId_returnsFilteredDtos() {
        when(worklogRepository.findByUserId(1L)).thenReturn(List.of(worklog));

        List<WorklogDto> result = worklogService.getWorklogsByUserId(1L);

        assertEquals(1, result.size());
        assertEquals(1L, result.get(0).getUserId());
    }

    @Test
    void createWorklog_validUser_savesAndReturnsDto() {
        WorklogDto input = new WorklogDto(null, LocalDate.now(), 1L, null, null, BigDecimal.valueOf(7.5), 1, 0);
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(worklogRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        WorklogDto result = worklogService.createWorklog(input);

        assertEquals(1, result.getMealsOrdered());
        assertEquals("Jan", result.getUserName());
        assertEquals(BigDecimal.valueOf(7.5), result.getTimeSpent());
        assertEquals("Kowalski", result.getUserSurname());
        assertEquals(1L, result.getUserId());
        assertEquals(0, result.getNightsSpent());
    }

    @Test
    void createWorklog_invalidUser_throwsException() {
        WorklogDto input = new WorklogDto(null, LocalDate.now(), 99L, null, null, BigDecimal.ONE, 0, 0);
        when(userRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> {
            worklogService.createWorklog(input);
        });
    }

    @Test
    void updateWorklog_existingWorklog_updatesAndReturnsDto() {
        WorklogDto update = new WorklogDto(1L, LocalDate.now(), 1L, null, null, BigDecimal.valueOf(9.0), 3, 2);
        when(worklogRepository.findById(1L)).thenReturn(Optional.of(worklog));
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(worklogRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        Optional<WorklogDto> result = worklogService.updateWorklog(1L, update);

        assertTrue(result.isPresent());
        assertEquals(3, result.get().getMealsOrdered());
        assertEquals(2, result.get().getNightsSpent());
    }

    @Test
    void deleteWorklog_existingId_deletesAndReturnsTrue() {
        when(worklogRepository.existsById(1L)).thenReturn(true);

        boolean result = worklogService.deleteWorklog(1L);

        assertTrue(result);
        verify(worklogRepository).deleteById(1L);
    }

    @Test
    void resolveUserIdByUsername_returnsIdWhenLinked() {
        when(accountRepository.findByUsername("jan")).thenReturn(Optional.of(account));

        Long resolved = worklogService.resolveUserIdByUsername("jan");

        assertEquals(1L, resolved);
    }

    @Test
    void resolveUserIdByUsername_returnsNullWhenUnknown() {
        when(accountRepository.findByUsername("ghost")).thenReturn(Optional.empty());

        assertNull(worklogService.resolveUserIdByUsername("ghost"));
    }

    @Test
    void resolveUserIdByUsername_returnsNullWhenAccountWithoutUser() {
        Account orphan = Account.builder().id(6L).username("orphan").password("pwd").role("ROLE_USER").build();
        when(accountRepository.findByUsername("orphan")).thenReturn(Optional.of(orphan));

        assertNull(worklogService.resolveUserIdByUsername("orphan"));
    }
}
