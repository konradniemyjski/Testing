
package com.michalstankiewicz.worklog.auth;

import com.michalstankiewicz.worklog.repository.AccountRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DbUserDetailsService implements UserDetailsService {
    private final AccountRepository repo;
    public DbUserDetailsService(AccountRepository repo) { this.repo = repo; }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        var acc = repo.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("No user: " + username));
        return new User(acc.getUsername(), acc.getPassword(), List.of(new SimpleGrantedAuthority(acc.getRole())));
    }
}
