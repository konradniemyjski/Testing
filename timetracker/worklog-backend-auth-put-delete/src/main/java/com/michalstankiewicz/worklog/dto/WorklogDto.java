package com.michalstankiewicz.worklog.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class WorklogDto {
    private Long id;
    private LocalDate workDate;
    private Long userId;
    private String userName; // Include user name for display
    private String userSurname; // Include user surname for display
    private BigDecimal timeSpent;
    private Integer mealsOrdered;
    private Integer nightsSpent;
}
