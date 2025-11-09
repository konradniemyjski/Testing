
package com.michalstankiewicz.worklog.auth;

import com.michalstankiewicz.worklog.model.Account;
import com.michalstankiewicz.worklog.model.User;
import com.michalstankiewicz.worklog.repository.AccountRepository;
import com.michalstankiewicz.worklog.repository.UserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtService jwt;
    private final AccountRepository accounts;
    private final PasswordEncoder encoder;
    private final UserRepository users;

    public AuthController(AuthenticationManager authenticationManager, JwtService jwt, AccountRepository accounts, PasswordEncoder encoder, UserRepository users) {
        this.authenticationManager = authenticationManager;
        this.jwt = jwt;
        this.accounts = accounts;
        this.encoder = encoder;
        this.users = users;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody AuthRequest req) {
        Authentication auth = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(req.getUsername(), req.getPassword())
        );
        String role = auth.getAuthorities().stream().map(GrantedAuthority::getAuthority).findFirst().orElse("ROLE_USER");
        String token = jwt.generate(req.getUsername(), role);
        return ResponseEntity.ok(new AuthResponse(token, role));
    }

    @PostMapping("/register")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> register(@RequestBody Map<String,String> payload) {
        String username = payload.get("username");
        String password = payload.get("password");
        String role = payload.getOrDefault("role", "ROLE_USER");
        String userIdRaw = payload.get("userId");

        if (accounts.existsByUsername(username)) {
            return ResponseEntity.badRequest().body(Map.of("error","username_taken"));
        }

        User user = null;
        if (userIdRaw != null && !userIdRaw.isBlank()) {
            try {
                Long userId = Long.valueOf(userIdRaw);
                if (accounts.findByUser_Id(userId).isPresent()) {
                    return ResponseEntity.badRequest().body(Map.of("error", "user_already_linked"));
                }
                user = users.findById(userId)
                        .orElseThrow(() -> new IllegalArgumentException("Invalid user ID: " + userId));
            } catch (NumberFormatException ex) {
                return ResponseEntity.badRequest().body(Map.of("error", "invalid_user_id"));
            } catch (IllegalArgumentException ex) {
                return ResponseEntity.badRequest().body(Map.of("error", "user_not_found"));
            }
        }

        accounts.save(Account.builder()
                .username(username)
                .password(encoder.encode(password))
                .role(role)
                .user(user)
                .build());
        return ResponseEntity.ok(Map.of("status","ok"));
    }
}
