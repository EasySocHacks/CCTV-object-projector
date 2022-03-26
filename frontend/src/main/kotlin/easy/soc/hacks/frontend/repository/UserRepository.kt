package easy.soc.hacks.frontend.repository

import easy.soc.hacks.frontend.domain.User
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.*

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun getUserByLoginAndPassword(login: String, password: String): Optional<User>

    fun getUserByLogin(login: String): Optional<User>
}