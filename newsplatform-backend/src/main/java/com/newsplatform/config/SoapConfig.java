package com.newsplatform.config;

import com.newsplatform.soap.UserWebService;
import jakarta.xml.ws.Endpoint;
import org.apache.cxf.Bus;
import org.apache.cxf.jaxws.EndpointImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SoapConfig {

    @Autowired
    private Bus bus;

    @Autowired
    private UserWebService userWebService;

    @Bean
    public Endpoint userServiceEndpoint() {
        EndpointImpl endpoint = new EndpointImpl(bus, userWebService);
        endpoint.publish("/users");
        return endpoint;
    }
}