package easy.soc.hacks.frontend.services

import easy.soc.hacks.frontend.domains.CalibrationPoint
import easy.soc.hacks.frontend.repositories.CalibrationPointRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class CalibrationPointService {
    @Autowired
    private lateinit var calibrationPointRepository: CalibrationPointRepository

    fun save(calibrationPoint: CalibrationPoint) = calibrationPointRepository.save(calibrationPoint)
}