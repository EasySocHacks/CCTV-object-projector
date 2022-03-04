package easy.soc.hacks.frontend.domain

import javax.persistence.*

@Embeddable
class Calibration(
    var p11: Double = 0.0,
    var p12: Double = 0.0,
    var p13: Double = 0.0,
    var p14: Double = 0.0,
    var p21: Double = 0.0,
    var p22: Double = 0.0,
    var p23: Double = 0.0,
    var p24: Double = 0.0,
    var p31: Double = 0.0,
    var p32: Double = 0.0,
    var p33: Double = 0.0,
    var p34: Double = 0.0
) {
    fun p(): List<List<Double>> {
        return listOf(
            listOf(p11, p12, p13, p14),
            listOf(p21, p22, p23, p24),
            listOf(p31, p32, p33, p34)
        )
    }
}

@Entity
class CalibrationPoint {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    lateinit var id: String

    var xScreen: Double = 0.0
    var yScreen: Double = 0.0
    var xWorld: Double = 0.0
    var yWorld: Double = 0.0
    var zWorld: Double = 0.0
}