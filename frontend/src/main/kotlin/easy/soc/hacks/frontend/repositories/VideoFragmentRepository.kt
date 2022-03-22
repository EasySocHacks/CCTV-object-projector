package easy.soc.hacks.frontend.repositories

import easy.soc.hacks.frontend.domains.Video
import easy.soc.hacks.frontend.domains.VideoFragment
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.*

@Repository
interface VideoFragmentRepository : JpaRepository<VideoFragment, Long> {
    fun getTop2ByVideoOrderByIdDesc(video: Video): List<VideoFragment>

    fun getVideoFragmentByVideoAndId(video: Video, int: Long): Optional<VideoFragment>
}