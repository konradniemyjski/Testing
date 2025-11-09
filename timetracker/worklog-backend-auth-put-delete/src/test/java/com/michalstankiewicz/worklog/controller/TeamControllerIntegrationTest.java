package com.michalstankiewicz.worklog.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.michalstankiewicz.worklog.dto.TeamDto;
import com.michalstankiewicz.worklog.model.Team;
import com.michalstankiewicz.worklog.repository.TeamRepository;
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
class TeamControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setup() {
        teamRepository.deleteAll();
    }

    @Test
    void createAndGetTeam() throws Exception {
        TeamDto teamDto = new TeamDto(null, "TestTeam");

        // Create
        mockMvc.perform(post("/api/teams")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(teamDto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("TestTeam"));

        // Get All
        mockMvc.perform(get("/api/teams"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].name").value("TestTeam"));
    }

    @Test
    void getNonExistingTeam_returns404() throws Exception {
        mockMvc.perform(get("/api/teams/999"))
                .andExpect(status().isNotFound());
    }

    @Test
    void deleteTeam() throws Exception {
        Team team = teamRepository.save(new Team(null, "ToDelete", List.of()));

        mockMvc.perform(delete("/api/teams/" + team.getId()))
                .andExpect(status().isNoContent());

        assertFalse(teamRepository.existsById(team.getId()));
    }
}
