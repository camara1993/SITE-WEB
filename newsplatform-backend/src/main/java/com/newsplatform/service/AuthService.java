package com.newsplatform.service;

import com.newsplatform.entity.AuthToken;
import com.newsplatform.entity.User;
import com.newsplatform.repository.AuthTokenRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Transactional
public class AuthService {

    private final AuthTokenRepository authTokenRepository;

    public AuthToken createToken(String description, User createdBy, LocalDateTime expiresAt) {
        AuthToken token = new AuthToken();
        token.setToken(generateUniqueToken());
        token.setDescription(description);
        token.setCreatedBy(createdBy);
        token.setExpiresAt(expiresAt);

        return authTokenRepository.save(token);
    }

    public Optional<AuthToken> validateToken(String token) {
        Optional<AuthToken> authToken = authTokenRepository.findByTokenAndActiveTrue(token);

        authToken.ifPresent(t -> {
            if (t.getExpiresAt() != null && t.getExpiresAt().isBefore(LocalDateTime.now())) {
                t.setActive(false);
                authTokenRepository.save(t);
                return;
            }
            t.setLastUsedAt(LocalDateTime.now());
            authTokenRepository.save(t);
        });

        return authToken.filter(AuthToken::isActive);
    }

    public void revokeToken(String token) {
        authTokenRepository.findByTokenAndActiveTrue(token).ifPresent(t -> {
            t.setActive(false);
            authTokenRepository.save(t);
        });
    }

    public void revokeTokenById(Long id) {
        AuthToken token = authTokenRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Token non trouvé avec l'ID: " + id));

        if (!token.isActive()) {
            throw new RuntimeException("Le token est déjà révoqué");
        }

        token.setActive(false);
        authTokenRepository.save(token);
    }

    public List<AuthToken> getAllTokens() {
        return authTokenRepository.findAll();
    }

    public Optional<AuthToken> getTokenById(Long id) {
        return authTokenRepository.findById(id);
    }

    public List<AuthToken> getActiveTokens() {
        return authTokenRepository.findAll().stream()
                .filter(AuthToken::isActive)
                .toList();
    }

    public List<AuthToken> getTokensByUser(User user) {
        return authTokenRepository.findAll().stream()
                .filter(token -> token.getCreatedBy().getId().equals(user.getId()))
                .toList();
    }

    private String generateUniqueToken() {
        String token;
        do {
            token = UUID.randomUUID().toString();
        } while (authTokenRepository.findByTokenAndActiveTrue(token).isPresent());

        return token;
    }
}