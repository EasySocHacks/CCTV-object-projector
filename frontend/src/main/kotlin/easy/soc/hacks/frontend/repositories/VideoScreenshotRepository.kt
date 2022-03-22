package easy.soc.hacks.frontend.repositories

import easy.soc.hacks.frontend.domains.VideoScreenshot
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface VideoScreenshotRepository: JpaRepository<VideoScreenshot, Long>