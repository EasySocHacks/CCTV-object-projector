package easy.soc.hacks.frontend.domain

import lombok.Data
import javax.persistence.*

@Table
@Entity
@Data
class VideoFragment {
    companion object {
        @Transient
        const val sequenceName = "VIDEO_FRAGMENT_SEQUENCE"
    }

    @Id
    @Column(nullable = false)
    var id: Long? = null

    @Column(nullable = false)
    var duration: Double? = null

    @Column(nullable = false)
    var data: ByteArray? = null

    @Id
    @Column(nullable = false)
    @OneToOne
    var video: Video? = null
}

open class VideoFragmentNode(
    val videoFragment: VideoFragment,
    var next: VideoFragmentNode? = null
)

class DummyVideoFragmentNode : VideoFragmentNode(VideoFragment().apply {
    id = -1
    duration = 0.0
    data = ByteArray(0)
})