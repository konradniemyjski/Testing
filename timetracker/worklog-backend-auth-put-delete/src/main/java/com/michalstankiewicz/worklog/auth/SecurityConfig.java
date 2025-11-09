package com.michalstankiewicz.worklog.auth;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableMethodSecurity // <-- to pozwala działać @PreAuthorize w AuthController.register
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;
    private final UserDetailsService userDetailsService;

    public SecurityConfig(JwtAuthFilter jwtAuthFilter, UserDetailsService userDetailsService) {
        this.jwtAuthFilter = jwtAuthFilter;
        this.userDetailsService = userDetailsService;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // nie używamy cookies CSRF, tylko JWT
            .csrf(csrf -> csrf.disable())

            // pozwól przeglądarce z localhost:4200 gadać z backendem na 8080
            .cors(Customizer.withDefaults())

            // bezstanowo - JWT w nagłówku Authorization
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

            // reguły dostępu
            .authorizeHttpRequests(auth -> auth
                // przeglądarka wysyła najpierw OPTIONS przy POSTach, to musi być dozwolone
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()

                // logowanie jest publiczne (każdy musi móc uderzyć /api/auth/login)
                .requestMatchers(HttpMethod.POST, "/api/auth/login").permitAll()

                // rejestracja NIE jest publiczna!
                // w kodzie kontrolera jest @PreAuthorize("hasRole('ADMIN')")
                // tu mówimy Springowi: endpoint wymaga autoryzacji JWT
                .requestMatchers(HttpMethod.POST, "/api/auth/register").authenticated()

                // listing /api/users/** tylko dla ADMIN
                .requestMatchers("/api/users/**").hasRole("ADMIN")

                // modyfikacja zespołów tylko ADMIN
                .requestMatchers(HttpMethod.POST,   "/api/teams/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.PUT,    "/api/teams/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.DELETE, "/api/teams/**").hasRole("ADMIN")

                // worklogi tylko dla zalogowanych, a w serwisie sprawdzamy właściciela
                .requestMatchers("/api/worklogs/**").authenticated()

                // wszystko inne też wymaga zalogowania
                .anyRequest().authenticated()
            )

            // httpBasic może zostać, nie przeszkadza
            .httpBasic(Customizer.withDefaults())

            // nasz filtr JWT ma być przed filtrem UsernamePasswordAuthenticationFilter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    // CORS konfiguracja
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration cfg = new CorsConfiguration();
        cfg.setAllowedOriginPatterns(List.of(
                "http://localhost:*",
                "https://localhost:*",
                "http://127.0.0.1:*",
                "https://127.0.0.1:*",
                "http://0.0.0.0:*",
                "https://0.0.0.0:*",
                "http://[::1]:*",
                "https://[::1]:*",
                "http://192.168.*:*",
                "https://192.168.*:*"
        ));
        cfg.setAllowedMethods(List.of("GET","POST","PUT","DELETE","OPTIONS","PATCH"));
        cfg.setAllowedHeaders(List.of("*"));
        cfg.setExposedHeaders(List.of("Authorization","Content-Disposition"));
        cfg.setAllowCredentials(true);
        cfg.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", cfg);
        return source;
    }

    // hashowanie haseł
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // Spring Security ma używać naszego userDetailsService + bcrypt
    @Bean
    public AuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    // AuthenticationManager używany w AuthController.login()
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
}
