package easy.soc.hacks.frontend.domain

import lombok.Data
import javax.persistence.*
import javax.persistence.InheritanceType.JOINED

@Table
@Entity
@Inheritance(strategy = JOINED)
@Data
class Video(
    @Id
    @Column(nullable = false)
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false)
    val name: String,

    @Column(nullable = false)
    @OneToMany
    val calibrationPointList: List<CalibrationPoint> = emptyList()
)

@Table
@Entity
@Data
class CameraVideo(
    id: Long? = null,
    name: String,
    calibrationPointList: List<CalibrationPoint> = emptyList(),

    @Column(nullable = false)
    val url: String
) : Video(id, name, calibrationPointList)

@Table
@Entity
@Data
class FileVideo(
    id: Long? = null,
    name: String,
    calibrationPointList: List<CalibrationPoint> = emptyList(),

    @Column(nullable = false)
    val path: String
) : Video(id, name, calibrationPointList)