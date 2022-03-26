package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.User
import easy.soc.hacks.frontend.domain.UserRole.ADMIN
import easy.soc.hacks.frontend.repository.UserRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import java.util.*

@Service
class UserService {
    @Autowired
    private lateinit var userRepository: UserRepository

    fun save(user: User): Optional<User> {
        if (user.role == ADMIN && getAdmin().isPresent) {
            return Optional.empty()
        }

        return try {
            Optional.of(userRepository.save(user))
        } catch (e: IllegalArgumentException) {
            Optional.empty()
        }
    }

    fun login(login: String, password: String): Optional<User> {
        val foundUser = userRepository.getUserByLogin(login).orElseGet { null }

        return if (foundUser?.password == User.encryptPassword(password, foundUser.salt)) {
            Optional.of(foundUser)
        } else {
            Optional.empty()
        }
    }

    fun getAdmin() = userRepository.getUserByLogin("admin")

    fun saveAdmin() = userRepository.save(User(
        login = "admin",
        role = ADMIN
    ).apply {
        password = "admin"
    })
}