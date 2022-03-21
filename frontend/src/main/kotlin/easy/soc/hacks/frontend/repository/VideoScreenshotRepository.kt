package easy.soc.hacks.frontend.repository

import easy.soc.hacks.frontend.domain.VideoScreenshot
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface VideoScreenshotRepository: JpaRepository<VideoScreenshot, Long>