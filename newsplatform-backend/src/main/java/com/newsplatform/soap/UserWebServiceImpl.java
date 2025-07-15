package com.newsplatform.soap;

import com.newsplatform.entity.AuthToken;
import com.newsplatform.entity.User;
import com.newsplatform.service.AuthService;
import com.newsplatform.service.UserService;
import jakarta.jws.WebService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@WebService(endpointInterface = "com.newsplatform.soap.UserWebService")
@RequiredArgsConstructor
public class UserWebServiceImpl implements UserWebService {

    private final UserService userService;
    private final AuthService authService;

    private void validateAdminToken(String authToken) {
        AuthToken token = authService.validateToken(authToken)
                .orElseThrow(() -> new RuntimeException("Invalid or expired token"));

        if (token.getCreatedBy().getRole() != User.UserRole.ADMIN) {
            throw new RuntimeException("Insufficient permissions");
        }
    }

    @Override
    public List<User> listUsers(String authToken) {
        validateAdminToken(authToken);
        return userService.getAllUsers();
    }

    @Override
    public User addUser(String authToken, User user) {
        validateAdminToken(authToken);
        return userService.createUser(user);
    }

    @Override
    public User updateUser(String authToken, Long userId, User user) {
        validateAdminToken(authToken);
        return userService.updateUser(userId, user);
    }

    @Override
    public void deleteUser(String authToken, Long userId) {
        validateAdminToken(authToken);
        userService.deleteUser(userId);
    }

    @Override
    public boolean authenticateUser(String username, String password) {
        return userService.authenticateUser(username, password);
    }
}