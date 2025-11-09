
package com.michalstankiewicz.worklog.repository;

import com.michalstankiewicz.worklog.model.Account;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AccountRepository extends JpaRepository<Account, Long> {
    Optional<Account> findByUsername(String username);
    boolean existsByUsername(String username);
    Optional<Account> findByUser_Id(Long userId);
}
