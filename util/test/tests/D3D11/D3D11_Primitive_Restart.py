import rdtest
import renderdoc as rd


class D3D11_Primitive_Restart(rdtest.TestCase):
    demos_test_name = 'D3D11_Primitive_Restart'

    def check_capture(self):
        draw = self.find_draw("Draw")

        self.check(draw is not None)

        self.controller.SetFrameEvent(draw.eventId, False)

        pipe: rd.PipeState = self.controller.GetPipelineState()

        postvs_data = self.get_postvs(draw, rd.MeshDataStage.VSOut, 0, draw.numIndices)

        # Calculate the strip restart index for this index width
        striprestart_index = pipe.GetStripRestartIndex() & ((1 << (draw.indexByteWidth*8)) - 1)

        # We don't check all of the output, we check a few key vertices to ensure they match up
        postvs_ref = {
            0: {
                'vtx': 0,
                'idx': 0,
                'SV_POSITION': [-0.8, 0.2, 0.0, 1.0],
                'COLOR': [0.0, 1.0, 0.0, 1.0],
                'TEXCOORD': [0.0, 0.0],
            },
            4: {
                'vtx': 4,
                'idx': 4,
                'SV_POSITION': [0.0, 0.2, 0.0, 1.0],
                'COLOR': [0.0, 1.0, 0.0, 1.0],
                'TEXCOORD': [0.0, 0.0],
            },
            8: {
                'idx': striprestart_index
            },
            9: {
                'vtx': 9,
                'idx': 8,
                'SV_POSITION': [-0.8, -0.7, 0.0, 1.0],
                'COLOR': [0.0, 0.0, 1.0, 1.0],
                'TEXCOORD': [0.0, 0.0],
            },
        }

        self.check_mesh_data(postvs_ref, postvs_data)

        # Now check the draw with a vertex offset
        draw = self.find_draw("Draw", draw.eventId+1)

        self.check(draw is not None)

        self.controller.SetFrameEvent(draw.eventId, False)

        postvs_data = self.get_postvs(draw, rd.MeshDataStage.VSOut, 0, draw.numIndices)

        # Data should be identical

        self.check_mesh_data(postvs_ref, postvs_data)

        # Check that the rendered mesh is as expected
        out = pipe.GetOutputTargets()[0].resourceId
        for x in [x*0.01 for x in range(1, 100)]:
            self.check_pixel_value(out, x, 0.1, [0.2, 0.2, 0.2, 1.0])
            self.check_pixel_value(out, x, 0.5, [0.2, 0.2, 0.2, 1.0])

        self.check_pixel_value(out, 0.3, 0.25, [0.0, 1.0, 0.0, 1.0])
        self.check_pixel_value(out, 0.5, 0.25, [0.0, 1.0, 0.0, 1.0])
        self.check_pixel_value(out, 0.7, 0.25, [0.0, 1.0, 0.0, 1.0])
        self.check_pixel_value(out, 0.3, 0.75, [0.0, 0.0, 1.0, 1.0])
        self.check_pixel_value(out, 0.5, 0.75, [0.0, 0.0, 1.0, 1.0])
        self.check_pixel_value(out, 0.7, 0.75, [0.0, 0.0, 1.0, 1.0])

