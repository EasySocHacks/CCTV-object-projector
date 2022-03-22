package easy.soc.hacks.frontend.domain

import lombok.Data
import javax.persistence.*

@Table
@Entity
@Data
class VideoFragment(
    @Id
    @Column(nullable = false)
    val id: Long? = null,

    @Column(nullable = false)
    val duration: Double,

    @Column(nullable = false)
    val data: ByteArray,

    @OneToOne
    val video: Video
)