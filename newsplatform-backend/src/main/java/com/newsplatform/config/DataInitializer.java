package com.newsplatform.config;

import com.newsplatform.entity.User;
import com.newsplatform.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
@Slf4j
public class DataInitializer {

    private final UserService userService;

    @Bean
    CommandLineRunner initDatabase() {
        return args -> {
            // Vérifier si un admin existe déjà
            if (!userService.getUserByUsername("admin").isPresent()) {
                // Créer un utilisateur admin
                User admin = new User();
                admin.setUsername("admin");
                admin.setPassword("admin123"); // Le service va l'encoder
                admin.setEmail("admin@newsplatform.com");
                admin.setFirstName("Admin");
                admin.setLastName("User");
                admin.setRole(User.UserRole.ADMIN);
                admin.setActive(true);

                try {
                    userService.createUser(admin);
                    log.info("Admin user created successfully!");
                } catch (Exception e) {
                    log.error("Error creating admin user: ", e);
                }
            }

            // Créer aussi un éditeur pour les tests
            if (!userService.getUserByUsername("editor").isPresent()) {
                User editor = new User();
                editor.setUsername("editor");
                editor.setPassword("editor123");
                editor.setEmail("editor@newsplatform.com");
                editor.setFirstName("Editor");
                editor.setLastName("User");
                editor.setRole(User.UserRole.EDITOR);
                editor.setActive(true);

                try {
                    userService.createUser(editor);
                    log.info("Editor user created successfully!");
                } catch (Exception e) {
                    log.error("Error creating editor user: ", e);
                }
            }
        };
    }
}