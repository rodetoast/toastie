import unittest
from types import SimpleNamespace

import ase_viewer


class RecoveryFxTests(unittest.TestCase):
    def test_particles_follow_player_and_expire(self):
        player = SimpleNamespace(x=10.0, y=200.0, particles=[])
        created = ase_viewer.spawn_player_recovery_fx(player)
        self.assertEqual(len(created), ase_viewer.RECOVERY_FX_PARTICLE_COUNT)
        self.assertTrue(all(p.owner is player for p in created))

        player.x = 35.0
        for particle in created:
            particle.update(ase_viewer.RECOVERY_FX_DURATION_MS + 1, 1, 500, [])
        self.assertTrue(all(p.lifetime <= 0 for p in created))
        self.assertTrue(any(abs(p.x - player.x) <= p.radius for p in created))

    def test_repeated_bursts_are_bounded_and_preserve_other_particles(self):
        player = SimpleNamespace(x=10.0, y=200.0, particles=[])
        ordinary = ase_viewer.Particle(0, 0, 0, 0, (255, 255, 255), 2, 1000)
        player.particles.append(ordinary)
        ase_viewer.spawn_player_recovery_fx(player)
        ase_viewer.spawn_player_recovery_fx(player)
        recovery = [
            p for p in player.particles if getattr(p, "is_recovery_fx", False)
        ]
        self.assertEqual(len(recovery), ase_viewer.RECOVERY_FX_PARTICLE_COUNT)
        self.assertIn(ordinary, player.particles)

    def test_missing_player_or_particle_list_is_safe(self):
        self.assertEqual(ase_viewer.spawn_player_recovery_fx(None), [])
        self.assertEqual(
            ase_viewer.spawn_player_recovery_fx(SimpleNamespace(x=0, y=0)),
            [],
        )


if __name__ == "__main__":
    unittest.main()
