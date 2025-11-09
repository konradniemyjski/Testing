package com.michalstankiewicz.worklog.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDate;
import java.math.BigDecimal;

@Entity
@EntityListeners(com.michalstankiewicz.worklog.model.WorklogEntityListener.class)
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Worklog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private LocalDate workDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false, precision = 4, scale = 2) // e.g., 99.75 hours
    private BigDecimal timeSpent;

    @Column(nullable = false)
    private Integer mealsOrdered;

    @Column(nullable = false)
    private Integer nightsSpent;

    @Column(name = "created_by")
    private String createdBy;

    // Convenience constructor kept for compatibility with older tests (without createdBy)
    public Worklog(Long id, java.time.LocalDate workDate, com.michalstankiewicz.worklog.model.User user,
                   java.math.BigDecimal timeSpent, Integer mealsOrdered, Integer nightsSpent) {
        this.id = id;
        this.workDate = workDate;
        this.user = user;
        this.timeSpent = timeSpent;
        this.mealsOrdered = mealsOrdered;
        this.nightsSpent = nightsSpent;
        this.createdBy = null;
    }

}
