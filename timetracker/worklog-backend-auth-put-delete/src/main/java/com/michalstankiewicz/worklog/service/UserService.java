package com.michalstankiewicz.worklog.service;

import com.michalstankiewicz.worklog.dto.UserDto;
import com.michalstankiewicz.worklog.model.Team;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.repository.TeamRepository;
import com.michalstankiewicz.worklog.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Transactional(readOnly = true)
    public List<UserDto> getAllUsers() {
        return userRepository.findAll().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<UserDto> getUserById(Long id) {
        return userRepository.findById(id).map(this::convertToDto);
    }

    @Transactional(readOnly = true)
    public List<UserDto> getUsersByTeamId(Long teamId) {
        return userRepository.findByTeamId(teamId).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public UserDto createUser(UserDto userDto) {
        Team team = teamRepository.findById(userDto.getTeamId())
                .orElseThrow(() -> new IllegalArgumentException("Invalid team ID: " + userDto.getTeamId()));
        User user = convertToEntity(userDto, team);
        User savedUser = userRepository.save(user);
        return convertToDto(savedUser);
    }

    @Transactional
    public Optional<UserDto> updateUser(Long id, UserDto userDto) {
        return userRepository.findById(id)
                .map(existingUser -> {
                    Team team = teamRepository.findById(userDto.getTeamId())
                            .orElseThrow(() -> new IllegalArgumentException("Invalid team ID: " + userDto.getTeamId()));
                    existingUser.setName(userDto.getName());
                    existingUser.setSurname(userDto.getSurname());
                    existingUser.setTeam(team);
                    User updatedUser = userRepository.save(existingUser);
                    return convertToDto(updatedUser);
                });
    }

    @Transactional
    public boolean deleteUser(Long id) {
        if (userRepository.existsById(id)) {
            // Consider implications if user has worklogs - cascade delete might handle this
            userRepository.deleteById(id);
            return true;
        }
        return false;
    }

    private UserDto convertToDto(User user) {
        return new UserDto(
                user.getId(),
                user.getName(),
                user.getSurname(),
                user.getTeam() != null ? user.getTeam().getId() : null,
                user.getTeam() != null ? user.getTeam().getName() : null
        );
    }

    private User convertToEntity(UserDto userDto, Team team) {
        User user = new User();
        // ID is not set here
        user.setName(userDto.getName());
        user.setSurname(userDto.getSurname());
        user.setTeam(team);
        // Worklogs list is managed via Worklog entity/service
        return user;
    }
}

