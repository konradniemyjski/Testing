
package com.michalstankiewicz.worklog.auth;

import com.michalstankiewicz.worklog.model.Account;
import com.michalstankiewicz.worklog.repository.AccountRepository;
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

    public AuthController(AuthenticationManager authenticationManager, JwtService jwt, AccountRepository accounts, PasswordEncoder encoder) {
        this.authenticationManager = authenticationManager;
        this.jwt = jwt;
        this.accounts = accounts;
        this.encoder = encoder;
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
        if (accounts.existsByUsername(username)) {
            return ResponseEntity.badRequest().body(Map.of("error","username_taken"));
        }
        accounts.save(Account.builder().username(username).password(encoder.encode(password)).role(role).build());
        return ResponseEntity.ok(Map.of("status","ok"));
    }
}
