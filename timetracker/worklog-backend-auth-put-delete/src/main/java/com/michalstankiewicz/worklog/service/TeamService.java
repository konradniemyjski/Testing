package com.michalstankiewicz.worklog.service;

import com.michalstankiewicz.worklog.dto.TeamDto;
import com.michalstankiewicz.worklog.model.Team;
import com.michalstankiewicz.worklog.repository.TeamRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class TeamService {

    @Autowired
    private TeamRepository teamRepository;

    @Transactional(readOnly = true)
    public List<TeamDto> getAllTeams() {
        return teamRepository.findAll().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<TeamDto> getTeamById(Long id) {
        return teamRepository.findById(id).map(this::convertToDto);
    }

    @Transactional
    public TeamDto createTeam(TeamDto teamDto) {
        // Check if team name already exists
        if (teamRepository.findByName(teamDto.getName()).isPresent()) {
            throw new IllegalArgumentException("Team name already exists: " + teamDto.getName());
        }
        Team team = convertToEntity(teamDto);
        Team savedTeam = teamRepository.save(team);
        return convertToDto(savedTeam);
    }

    @Transactional
    public Optional<TeamDto> updateTeam(Long id, TeamDto teamDto) {
        return teamRepository.findById(id)
                .map(existingTeam -> {
                    // Check for name conflict if name is being changed
                    if (!existingTeam.getName().equals(teamDto.getName()) &&
                            teamRepository.findByName(teamDto.getName()).isPresent()) {
                        throw new IllegalArgumentException("Team name already exists: " + teamDto.getName());
                    }
                    existingTeam.setName(teamDto.getName());
                    Team updatedTeam = teamRepository.save(existingTeam);
                    return convertToDto(updatedTeam);
                });
    }

    @Transactional
    public boolean deleteTeam(Long id) {
        if (teamRepository.existsById(id)) {
            // Consider adding logic to handle users associated with the team before deletion
            // For now, assuming cascade delete handles it or users should be reassigned first.
            teamRepository.deleteById(id);
            return true;
        }
        return false;
    }

    private TeamDto convertToDto(Team team) {
        return new TeamDto(team.getId(), team.getName());
    }

    private Team convertToEntity(TeamDto teamDto) {
        Team team = new Team();
        // ID is not set here as it's generated or used for updates
        team.setName(teamDto.getName());
        // Users list is managed via the User entity/service
        return team;
    }
}

