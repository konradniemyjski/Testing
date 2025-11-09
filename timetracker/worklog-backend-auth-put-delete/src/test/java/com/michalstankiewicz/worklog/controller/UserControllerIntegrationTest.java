package com.michalstankiewicz.worklog.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.michalstankiewicz.worklog.dto.UserDto;
import com.michalstankiewicz.worklog.model.Team;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.repository.TeamRepository;
import com.michalstankiewicz.worklog.repository.UserRepository;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private ObjectMapper objectMapper;

    private Team team;

    @BeforeEach
    void setup() {
        userRepository.deleteAll();
        teamRepository.deleteAll();
        team = teamRepository.save(new Team(null, "Backend", List.of()));
    }

    @Test
    void createAndGetUser() throws Exception {
        UserDto userDto = new UserDto(null, "Adam", "Nowak", team.getId(), null);

        // Create
        mockMvc.perform(post("/api/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(userDto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Adam"))
                .andExpect(jsonPath("$.teamId").value(team.getId()));

        // Get All
        mockMvc.perform(get("/api/users"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].name").value("Adam"));
    }

    @Test
    void getUserById_existing_returnsUser() throws Exception {
        User user = userRepository.save(new User(null, "Ewa", "Kowalska", team, List.of()));

        mockMvc.perform(get("/api/users/" + user.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Ewa"));
    }

    @Test
    void getUserById_notFound_returns404() throws Exception {
        mockMvc.perform(get("/api/users/9999"))
                .andExpect(status().isNotFound());
    }

    @Test
    void updateUser_existing_updatesAndReturnsUser() throws Exception {
        User user = userRepository.save(new User(null, "Ola", "Zielińska", team, List.of()));
        UserDto update = new UserDto(user.getId(), "Aleksandra", "Zielińska", team.getId(), null);

        mockMvc.perform(put("/api/users/" + user.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(update)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Aleksandra"));
    }

    @Test
    void deleteUser_existing_deletesAndReturnsNoContent() throws Exception {
        User user = userRepository.save(new User(null, "Piotr", "Lis", team, List.of()));

        mockMvc.perform(delete("/api/users/" + user.getId()))
                .andExpect(status().isNoContent());

        assertFalse(userRepository.existsById(user.getId()));
    }

    @Test
    void getUsersByTeamId_returnsFilteredUsers() throws Exception {
        Team team2 = teamRepository.save(new Team(null, "Frontend", List.of()));
        userRepository.save(new User(null, "A", "A", team, List.of()));
        userRepository.save(new User(null, "B", "B", team2, List.of()));

        mockMvc.perform(get("/api/users?teamId=" + team2.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].teamName").value("Frontend"));
    }
}
