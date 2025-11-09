package com.michalstankiewicz.worklog.service;

import com.michalstankiewicz.worklog.dto.UserDto;
import com.michalstankiewicz.worklog.model.Team;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.repository.TeamRepository;
import com.michalstankiewicz.worklog.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.*;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class UserServiceTest {

    @Mock
    private UserRepository userRepository;
    @Mock
    private TeamRepository teamRepository;

    @InjectMocks
    private UserService userService;

    private Team team;
    private User user;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        team = new Team(1L, "Dev Team", new ArrayList<>());
        user = new User(1L, "Jan", "Kowalski", team, new ArrayList<>());
    }

    @Test
    void getAllUsers_returnsListOfUserDtos() {
        when(userRepository.findAll()).thenReturn(List.of(user));

        List<UserDto> result = userService.getAllUsers();

        assertEquals(1, result.size());
        assertEquals("Jan", result.get(0).getName());
        assertEquals("Dev Team", result.get(0).getTeamName());
    }

    @Test
    void getUserById_existingId_returnsUserDto() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        Optional<UserDto> result = userService.getUserById(1L);

        assertTrue(result.isPresent());
        assertEquals("Jan", result.get().getName());
    }

    @Test
    void getUserById_nonExistingId_returnsEmptyOptional() {
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        Optional<UserDto> result = userService.getUserById(1L);

        assertFalse(result.isPresent());
    }

    @Test
    void getUsersByTeamId_returnsListOfUserDtos() {
        when(userRepository.findByTeamId(1L)).thenReturn(List.of(user));

        List<UserDto> result = userService.getUsersByTeamId(1L);

        assertEquals(1, result.size());
        assertEquals("Jan", result.get(0).getName());
    }

    @Test
    void createUser_validTeam_savesAndReturnsDto() {
        UserDto input = new UserDto(null, "Anna", "Nowak", 1L, null);
        when(teamRepository.findById(1L)).thenReturn(Optional.of(team));
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User u = inv.getArgument(0);
            u.setId(2L);
            return u;
        });

        UserDto result = userService.createUser(input);

        assertNotNull(result.getId());
        assertEquals("Anna", result.getName());
        assertEquals("Dev Team", result.getTeamName());
    }

    @Test
    void createUser_invalidTeam_throwsException() {
        UserDto input = new UserDto(null, "Anna", "Nowak", 99L, null);
        when(teamRepository.findById(99L)).thenReturn(Optional.empty());

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () -> {
            userService.createUser(input);
        });

        assertTrue(ex.getMessage().contains("Invalid team ID"));
    }

    @Test
    void updateUser_existingUser_validTeam_updatesAndReturnsDto() {
        UserDto update = new UserDto(1L, "Janek", "Kowalski", 1L, null);
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(teamRepository.findById(1L)).thenReturn(Optional.of(team));
        when(userRepository.save(any(User.class))).thenAnswer(inv -> inv.getArgument(0));

        Optional<UserDto> result = userService.updateUser(1L, update);

        assertTrue(result.isPresent());
        assertEquals("Janek", result.get().getName());
    }

    @Test
    void updateUser_existingUser_invalidTeam_throwsException() {
        UserDto update = new UserDto(1L, "Janek", "Kowalski", 99L, null);
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(teamRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> {
            userService.updateUser(1L, update);
        });
    }

    @Test
    void updateUser_nonExistingUser_returnsEmptyOptional() {
        UserDto update = new UserDto(1L, "Janek", "Kowalski", 1L, null);
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        Optional<UserDto> result = userService.updateUser(1L, update);

        assertFalse(result.isPresent());
    }

    @Test
    void deleteUser_existingId_deletesAndReturnsTrue() {
        when(userRepository.existsById(1L)).thenReturn(true);

        boolean result = userService.deleteUser(1L);

        assertTrue(result);
        verify(userRepository).deleteById(1L);
    }

    @Test
    void deleteUser_nonExistingId_returnsFalse() {
        when(userRepository.existsById(1L)).thenReturn(false);

        boolean result = userService.deleteUser(1L);

        assertFalse(result);
        verify(userRepository, never()).deleteById(anyLong());
    }
}
