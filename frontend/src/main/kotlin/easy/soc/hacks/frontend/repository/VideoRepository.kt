package easy.soc.hacks.frontend.repository

import easy.soc.hacks.frontend.domain.Video
import org.springframework.data.mongodb.repository.MongoRepository
import org.springframework.stereotype.Repository
import java.util.*

@Repository
interface VideoRepository : MongoRepository<Video, String> {
    fun getVideoById(id: Long): Optional<out Video>
}