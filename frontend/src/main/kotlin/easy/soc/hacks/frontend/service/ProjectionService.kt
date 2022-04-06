package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.Projection
import easy.soc.hacks.frontend.repository.ProjectionRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class ProjectionService {
    @Autowired
    private lateinit var projectionRepository: ProjectionRepository

    fun save(projection: Projection): Projection {
        val pointId = projectionRepository.save(
            batchId = projection.batchId,
            frameId = projection.frameId,
            sessionId = projection.session!!.id,
            radius = projection.radius,
            x = projection.x,
            y = projection.y
        )

        return Projection(
            pointId = pointId,
            batchId = projection.batchId,
            frameId = projection.frameId,
            session = projection.session,
            radius = projection.radius,
            x = projection.x,
            y = projection.y
        )
    }

    fun findProjectionsByBatchIdAndSessionId(batchId: Long, sessionId: String) =
        projectionRepository.findProjectionsByBatchIdAndSessionId(batchId, sessionId)
}