package easy.soc.hacks.frontend.repositories

import easy.soc.hacks.frontend.domains.Video
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.*


@Repository
interface VideoRepository : JpaRepository<Video, String> {
    fun getVideoById(id: Long): Optional<out Video>
}