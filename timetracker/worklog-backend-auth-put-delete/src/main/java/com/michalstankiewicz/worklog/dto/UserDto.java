package com.michalstankiewicz.worklog.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserDto {
    private Long id;
    private String name;
    private String surname;
    private Long teamId; // Only include team ID, not the full Team object
    private String teamName; // Optionally include team name for display
    // No worklogs list here
}


