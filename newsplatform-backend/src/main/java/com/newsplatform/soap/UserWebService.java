package com.newsplatform.soap;

import com.newsplatform.entity.User;
import jakarta.jws.WebMethod;
import jakarta.jws.WebParam;
import jakarta.jws.WebService;
import java.util.List;

@WebService
public interface UserWebService {

    @WebMethod
    List<User> listUsers(@WebParam(name = "authToken") String authToken);

    @WebMethod
    User addUser(@WebParam(name = "authToken") String authToken,
                 @WebParam(name = "user") User user);

    @WebMethod
    User updateUser(@WebParam(name = "authToken") String authToken,
                    @WebParam(name = "userId") Long userId,
                    @WebParam(name = "user") User user);

    @WebMethod
    void deleteUser(@WebParam(name = "authToken") String authToken,
                    @WebParam(name = "userId") Long userId);

    @WebMethod
    boolean authenticateUser(@WebParam(name = "username") String username,
                             @WebParam(name = "password") String password);
}