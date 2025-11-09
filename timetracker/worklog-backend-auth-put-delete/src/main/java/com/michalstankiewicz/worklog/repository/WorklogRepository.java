package com.michalstankiewicz.worklog.repository;

import com.michalstankiewicz.worklog.model.Worklog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface WorklogRepository extends JpaRepository<Worklog, Long> {
    List<Worklog> findByUserId(Long userId);
    List<Worklog> findByWorkDateBetween(LocalDate startDate, LocalDate endDate);
    List<Worklog> findByUserIdAndWorkDateBetween(Long userId, LocalDate startDate, LocalDate endDate);
}

