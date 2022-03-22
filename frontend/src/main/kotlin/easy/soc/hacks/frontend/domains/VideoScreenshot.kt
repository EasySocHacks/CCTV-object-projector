package easy.soc.hacks.frontend.domains

import lombok.Data
import javax.persistence.*

@Table
@Entity
@Data
class VideoScreenshot (
    @Id
    @Column(nullable = false)
    val videoId: Long? = null,

    @OneToOne
    @MapsId
    @JoinColumn(name = "videoId")
    val video: Video,

    @Column(nullable = false)
    val data: ByteArray
)