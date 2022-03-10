package easy.soc.hacks.frontend.domain

import javax.persistence.Column
import javax.persistence.Embeddable
import javax.persistence.Entity
import javax.persistence.Id

@Embeddable
class Calibration(
    @Column(nullable = false)
    var p11: Double? = null,

    @Column(nullable = false)
    var p12: Double? = null,

    @Column(nullable = false)
    var p13: Double? = null,

    @Column(nullable = false)
    var p14: Double? = null,

    @Column(nullable = false)
    var p21: Double? = null,

    @Column(nullable = false)
    var p22: Double? = null,

    @Column(nullable = false)
    var p23: Double? = null,

    @Column(nullable = false)
    var p24: Double? = null,

    @Column(nullable = false)
    var p31: Double? = null,

    @Column(nullable = false)
    var p32: Double? = null,

    @Column(nullable = false)
    var p33: Double? = null,

    @Column(nullable = false)
    var p34: Double? = null

) {
    fun p(): List<List<Double?>> {
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
    var id: Long? = null

    var xScreen: Double? = null
    var yScreen: Double? = null
    var xWorld: Double? = null
    var yWorld: Double? = null
    var zWorld: Double? = null
}

data class CalibrationPointListWrapper(
    val xScreen0: Double,
    val yScreen0: Double,
    val xWorld0: Double,
    val yWorld0: Double,
    val zWorld0: Double,

    val xScreen1: Double,
    val yScreen1: Double,
    val xWorld1: Double,
    val yWorld1: Double,
    val zWorld1: Double,

    val xScreen2: Double,
    val yScreen2: Double,
    val xWorld2: Double,
    val yWorld2: Double,
    val zWorld2: Double,

    val xScreen3: Double,
    val yScreen3: Double,
    val xWorld3: Double,
    val yWorld3: Double,
    val zWorld3: Double,

    val xScreen4: Double,
    val yScreen4: Double,
    val xWorld4: Double,
    val yWorld4: Double,
    val zWorld4: Double,

    val xScreen5: Double,
    val yScreen5: Double,
    val xWorld5: Double,
    val yWorld5: Double,
    val zWorld5: Double,
) {
    fun toCalibrationPointList(): List<CalibrationPoint> {
        return listOf(
            CalibrationPoint().apply {
                id = 0
                xScreen = xScreen0
                yScreen = yScreen0
                xWorld = xWorld0
                yWorld = yWorld0
                zWorld = zWorld0
            },

            CalibrationPoint().apply {
                id = 1
                xScreen = xScreen1
                yScreen = yScreen1
                xWorld = xWorld1
                yWorld = yWorld1
                zWorld = zWorld1
            },

            CalibrationPoint().apply {
                id = 2
                xScreen = xScreen2
                yScreen = yScreen2
                xWorld = xWorld2
                yWorld = yWorld2
                zWorld = zWorld2
            },

            CalibrationPoint().apply {
                id = 3
                xScreen = xScreen3
                yScreen = yScreen3
                xWorld = xWorld3
                yWorld = yWorld3
                zWorld = zWorld3
            },

            CalibrationPoint().apply {
                id = 4
                xScreen = xScreen4
                yScreen = yScreen4
                xWorld = xWorld4
                yWorld = yWorld4
                zWorld = zWorld4
            },

            CalibrationPoint().apply {
                id = 5
                xScreen = xScreen5
                yScreen = yScreen5
                xWorld = xWorld5
                yWorld = yWorld5
                zWorld = zWorld5
            }
        )
    }
}