package com.michalstankiewicz.worklog.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.michalstankiewicz.worklog.dto.WorklogDto;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.model.Worklog;
import com.michalstankiewicz.worklog.repository.UserRepository;
import com.michalstankiewicz.worklog.repository.WorklogRepository;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class WorklogControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private WorklogRepository worklogRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ObjectMapper objectMapper;

    private User user;

    @BeforeEach
    void setup() {
        worklogRepository.deleteAll();
        userRepository.deleteAll();
        user = userRepository.save(new User(null, "Test", "User", null, List.of()));
    }

    @Test
    void createAndRetrieveWorklog() throws Exception {
        WorklogDto dto = new WorklogDto(null, LocalDate.now(), user.getId(), null, null, BigDecimal.valueOf(8.0), 2, 1);

        mockMvc.perform(post("/api/worklogs")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.timeSpent").value(8.0));

        mockMvc.perform(get("/api/worklogs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    void exportWorklogs_returnsExcelFile() throws Exception {
        worklogRepository.save(new Worklog(null, LocalDate.now(), user, BigDecimal.valueOf(7.5), 1, 0));

        MockHttpServletResponse response = mockMvc.perform(get("/api/worklogs/export/xls"))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Disposition", containsString("worklogs.xlsx")))
                .andReturn().getResponse();

        assertTrue(response.getContentAsByteArray().length > 0);
    }

    @Test
    void getWorklogsByUserId_returnsFiltered() throws Exception {
        User user2 = userRepository.save(new User(null, "Another", "User", null, List.of()));
        worklogRepository.save(new Worklog(null, LocalDate.now(), user, BigDecimal.ONE, 0, 0));
        worklogRepository.save(new Worklog(null, LocalDate.now(), user2, BigDecimal.ONE, 0, 0));

        mockMvc.perform(get("/api/worklogs?userId=" + user.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].userName").value("Test"));
    }
}
