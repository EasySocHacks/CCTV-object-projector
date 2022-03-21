package easy.soc.hacks.frontend.repository

import easy.soc.hacks.frontend.domain.Video
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.*


@Repository
interface VideoRepository : JpaRepository<Video, String> {
    fun getVideoById(id: Long): Optional<out Video>
}