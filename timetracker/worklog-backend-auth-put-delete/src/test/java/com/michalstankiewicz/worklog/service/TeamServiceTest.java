package com.michalstankiewicz.worklog.service;

import com.michalstankiewicz.worklog.dto.TeamDto;
import com.michalstankiewicz.worklog.model.Team;
import com.michalstankiewicz.worklog.repository.TeamRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.*;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class TeamServiceTest {

    @Mock
    private TeamRepository teamRepository;

    @InjectMocks
    private TeamService teamService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void getAllTeams_returnsListOfTeamDtos() {
        List<Team> teams = List.of(new Team(1L, "Alpha", List.of()), new Team(2L, "Beta", List.of()));
        when(teamRepository.findAll()).thenReturn(teams);

        List<TeamDto> result = teamService.getAllTeams();

        assertEquals(2, result.size());
        assertEquals("Alpha", result.get(0).getName());
    }

    @Test
    void getTeamById_existingId_returnsTeamDto() {
        Team team = new Team(1L, "Alpha", List.of());
        when(teamRepository.findById(1L)).thenReturn(Optional.of(team));

        Optional<TeamDto> result = teamService.getTeamById(1L);

        assertTrue(result.isPresent());
        assertEquals("Alpha", result.get().getName());
    }

    @Test
    void getTeamById_nonExistingId_returnsEmptyOptional() {
        when(teamRepository.findById(1L)).thenReturn(Optional.empty());

        Optional<TeamDto> result = teamService.getTeamById(1L);

        assertFalse(result.isPresent());
    }

    @Test
    void createTeam_uniqueName_savesAndReturnsDto() {
        TeamDto input = new TeamDto(null, "Alpha");
        when(teamRepository.findByName("Alpha")).thenReturn(Optional.empty());
        Team saved = new Team(1L, "Alpha", List.of());
        when(teamRepository.save(any(Team.class))).thenReturn(saved);

        TeamDto result = teamService.createTeam(input);

        assertNotNull(result.getId());
        assertEquals("Alpha", result.getName());
    }

    @Test
    void createTeam_duplicateName_throwsException() {
        TeamDto input = new TeamDto(null, "Alpha");
        when(teamRepository.findByName("Alpha")).thenReturn(Optional.of(new Team()));

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () -> {
            teamService.createTeam(input);
        });

        assertTrue(ex.getMessage().contains("Team name already exists"));
    }

    @Test
    void updateTeam_existingId_uniqueName_updatesAndReturnsDto() {
        Team existing = new Team(1L, "Alpha", List.of());
        TeamDto update = new TeamDto(1L, "Beta");
        when(teamRepository.findById(1L)).thenReturn(Optional.of(existing));
        when(teamRepository.findByName("Beta")).thenReturn(Optional.empty());
        when(teamRepository.save(any(Team.class))).thenAnswer(i -> i.getArgument(0));

        Optional<TeamDto> result = teamService.updateTeam(1L, update);

        assertTrue(result.isPresent());
        assertEquals("Beta", result.get().getName());
    }

    @Test
    void updateTeam_existingId_duplicateName_throwsException() {
        Team existing = new Team(1L, "Alpha", List.of());
        TeamDto update = new TeamDto(1L, "Beta");
        when(teamRepository.findById(1L)).thenReturn(Optional.of(existing));
        when(teamRepository.findByName("Beta")).thenReturn(Optional.of(new Team()));

        assertThrows(IllegalArgumentException.class, () -> {
            teamService.updateTeam(1L, update);
        });
    }

    @Test
    void updateTeam_nonExistingId_returnsEmptyOptional() {
        TeamDto update = new TeamDto(1L, "Beta");
        when(teamRepository.findById(1L)).thenReturn(Optional.empty());

        Optional<TeamDto> result = teamService.updateTeam(1L, update);

        assertFalse(result.isPresent());
    }

    @Test
    void deleteTeam_existingId_deletesAndReturnsTrue() {
        when(teamRepository.existsById(1L)).thenReturn(true);

        boolean result = teamService.deleteTeam(1L);

        assertTrue(result);
        verify(teamRepository).deleteById(1L);
    }

    @Test
    void deleteTeam_nonExistingId_returnsFalse() {
        when(teamRepository.existsById(1L)).thenReturn(false);

        boolean result = teamService.deleteTeam(1L);

        assertFalse(result);
        verify(teamRepository, never()).deleteById(anyLong());
    }
}
