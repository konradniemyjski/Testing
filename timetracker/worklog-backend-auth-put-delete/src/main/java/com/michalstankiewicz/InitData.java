
package com.michalstankiewicz.worklog;

import com.michalstankiewicz.worklog.model.Account;
import com.michalstankiewicz.worklog.repository.AccountRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class InitData {
    @Bean
    CommandLineRunner seed(AccountRepository repo, PasswordEncoder enc) {
        return args -> {
            if (repo.count()==0) {
                repo.save(Account.builder().username("admin").password(enc.encode("admin123")).role("ROLE_ADMIN").build());
                repo.save(Account.builder().username("user").password(enc.encode("user123")).role("ROLE_USER").build());
            }
        };
    }
}
