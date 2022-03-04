package easy.soc.hacks.frontend.domain

import javax.persistence.Column
import javax.persistence.Entity
import javax.persistence.Id
import javax.persistence.Table

@Entity
@Table
class Sequence {
    @Id
    var id: String? = null

    @Column(nullable = false)
    var currentSequence: Long? = null
}