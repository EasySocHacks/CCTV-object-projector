package easy.soc.hacks.frontend.domain

import lombok.Data
import javax.persistence.*

@Table
@Entity
@Data
open class Video {
    companion object {
        @Transient
        const val sequenceName = "VIDEO_SEQUENCE"
    }

    @Id
    @Column(nullable = false)
    var id: Long? = null

    @Column(nullable = false)
    var name: String? = null

    @Column
    var calibration: Calibration? = null

    @Column
    @OneToMany
    var calibrationPointList = mutableListOf<CalibrationPoint>()
}

@Table
@Entity
@Data
class CameraVideo : Video() {
    @Column(nullable = false)
    var url: String? = null
}

@Table
@Entity
@Data
class FileVideo : Video() {
    @Column(nullable = false)
    var path: String? = null
}