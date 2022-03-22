package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.Video
import easy.soc.hacks.frontend.domain.VideoFragment
import easy.soc.hacks.frontend.repository.VideoFragmentRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class VideoFragmentService {
    @Autowired
    private lateinit var videoFragmentRepository: VideoFragmentRepository

    fun save(videoFragment: VideoFragment) = videoFragmentRepository.save(videoFragment)

    fun getLatestManifest(video: Video): ByteArray {
        val videoFragments = videoFragmentRepository.getTop2ByVideoOrderByIdDesc(video).reversed()
        val manifestTextStringBuffer = StringBuilder()

        manifestTextStringBuffer.append("#EXTM3U\n")
        manifestTextStringBuffer.append("#EXT-X-VERSION:3\n")
        manifestTextStringBuffer.append("#EXT-X-MEDIA-SEQUENCE:${videoFragments[0].id}\n")
        manifestTextStringBuffer.append("#EXT-X-TARGETDURATION:5\n")
        manifestTextStringBuffer.append(
            videoFragments.joinToString(separator = "\n") {
                "#EXTINF:${it.duration},\nfragment/${it.id}"
            }
        )

        return manifestTextStringBuffer.toString().toByteArray()
    }

    fun getVideoFragment(video: Video, id: Long) = videoFragmentRepository.getVideoFragmentByVideoAndId(video, id)
}