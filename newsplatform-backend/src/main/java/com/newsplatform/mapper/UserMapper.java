package com.newsplatform.mapper;

import com.newsplatform.dto.CreateUserRequest;
import com.newsplatform.entity.User;
import org.springframework.stereotype.Component;

@Component
public class UserMapper {

    public User toEntity(CreateUserRequest request) {
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(request.getPassword());
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());

        // Convertir le rôle string en enum
        if (request.getRole() != null) {
            try {
                user.setRole(User.UserRole.valueOf(request.getRole().toUpperCase()));
            } catch (IllegalArgumentException e) {
                throw new RuntimeException("Rôle invalide: " + request.getRole());
            }
        }

        // Définir active
        user.setActive(request.getActive() != null ? request.getActive() : true);

        return user;
    }
}