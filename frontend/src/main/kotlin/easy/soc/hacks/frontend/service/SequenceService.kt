package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.Sequence
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.data.mongodb.core.FindAndModifyOptions.options
import org.springframework.data.mongodb.core.MongoOperations
import org.springframework.data.mongodb.core.query.Criteria.where
import org.springframework.data.mongodb.core.query.Query.query
import org.springframework.data.mongodb.core.query.Update
import org.springframework.stereotype.Service

@Service
class SequenceService {
    @Autowired
    private lateinit var mongoOperations: MongoOperations

    fun nextIdFor(sequenceName: String): Long {
        return mongoOperations.findAndModify(
            query(where("_id").`is`(sequenceName)),
            Update().inc("currentSequence", 1),
            options().returnNew(true).upsert(true),
            Sequence::class.java
        ).let {
            return@let if (it == null) {
                mongoOperations.save(Sequence().apply {
                    id = sequenceName
                    currentSequence = 0L
                })

                0L
            } else {
                it.currentSequence!!
            }
        }
    }
}