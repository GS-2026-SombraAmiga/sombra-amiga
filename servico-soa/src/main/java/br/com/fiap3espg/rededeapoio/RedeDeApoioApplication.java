package br.com.fiap3espg.rededeapoio;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.web.config.EnableSpringDataWebSupport;

import static org.springframework.data.web.config.EnableSpringDataWebSupport.PageSerializationMode.VIA_DTO;

// VIA_DTO: as paginas saem em um JSON estavel ({content, page}) em vez da
// serializacao interna do PageImpl, que o Spring Data desaconselha.
@SpringBootApplication
@EnableSpringDataWebSupport(pageSerializationMode = VIA_DTO)
public class RedeDeApoioApplication {

	public static void main(String[] args) {
		SpringApplication.run(RedeDeApoioApplication.class, args);
	}

}
