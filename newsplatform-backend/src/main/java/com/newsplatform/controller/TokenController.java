package com.newsplatform.controller;

import com.newsplatform.dto.TokenDTO;
import com.newsplatform.entity.AuthToken;
import com.newsplatform.entity.User;
import com.newsplatform.service.AuthService;
import com.newsplatform.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/tokens")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
@CrossOrigin(origins = "http://localhost:3000")
public class TokenController {

    private final AuthService authService;
    private final UserService userService;

    @GetMapping
    public ResponseEntity<List<TokenDTO>> getAllTokens() {
        List<AuthToken> tokens = authService.getAllTokens();
        List<TokenDTO> tokenDTOs = tokens.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(tokenDTOs);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TokenDTO> getToken(@PathVariable Long id) {
        return authService.getTokenById(id)
                .map(token -> ResponseEntity.ok(convertToDTO(token)))
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<?> createToken(@RequestBody Map<String, Object> request, Authentication authentication) {
        try {
            String description = (String) request.get("description");
            String expiresAtStr = (String) request.get("expiresAt");

            User currentUser = userService.getUserByUsername(authentication.getName())
                    .orElseThrow(() -> new RuntimeException("User not found"));

            LocalDateTime expiresAt = null;
            if (expiresAtStr != null && !expiresAtStr.isEmpty()) {
                expiresAt = LocalDateTime.parse(expiresAtStr);
            }

            AuthToken token = authService.createToken(description, currentUser, expiresAt);

            Map<String, Object> response = new HashMap<>();
            response.put("token", token.getToken());
            response.put("id", token.getId());
            response.put("description", token.getDescription());
            response.put("createdAt", token.getCreatedAt());
            response.put("expiresAt", token.getExpiresAt());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> revokeToken(@PathVariable Long id) {
        try {
            authService.revokeTokenById(id);
            return ResponseEntity.ok(Map.of("message", "Token révoqué avec succès"));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Erreur lors de la révocation du token: " + e.getMessage()));
        }
    }

    @PutMapping("/{id}/revoke")
    public ResponseEntity<?> revokeTokenByUpdate(@PathVariable Long id) {
        try {
            authService.revokeTokenById(id);
            return ResponseEntity.ok(Map.of("message", "Token révoqué avec succès"));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Erreur lors de la révocation du token: " + e.getMessage()));
        }
    }

    private TokenDTO convertToDTO(AuthToken token) {
        TokenDTO dto = new TokenDTO();
        dto.setId(token.getId());
        dto.setToken(token.getToken());
        dto.setDescription(token.getDescription());
        dto.setCreatedBy(token.getCreatedBy().getUsername());
        dto.setCreatedAt(token.getCreatedAt());
        dto.setExpiresAt(token.getExpiresAt());
        dto.setActive(token.isActive());
        dto.setLastUsedAt(token.getLastUsedAt());
        return dto;
    }
}