package com.michalstankiewicz.worklog.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TeamDto {
        private Long id;
        private String name;
        // No users list here to avoid circular dependencies and large payloads
}

