package easy.soc.hacks.frontend.repositories

import easy.soc.hacks.frontend.domains.CalibrationPoint
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface CalibrationPointRepository : JpaRepository<CalibrationPoint, Long>