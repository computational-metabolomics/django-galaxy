from bioblend import galaxy

gi = galaxy.GalaxyInstance(url='http://127.0.0.1:8099', key='1c9ccfd1caaa952a42cc637d4079f022')
gi.verify = False
tc = galaxy.tools.ToolClient(gi)
tcs = galaxy.toolshed.ToolShedClient(gi)

###########################################################################################################
# msPurity
###########################################################################################################
tool_panel_section = 'mspurity'
tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='anticipated_purity_dims',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='3e24ab185347')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='anticipated_purity_lcms',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='b83bcc259b76')


tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='assess_purity_msms',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='146699c00d38')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='create_sqlite_db',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='1a88758357ed')


tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='spectral_matching',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='84d223e361c6')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='track_rt_raw',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='26fd52ed6d21')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='frag4feature',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='8a9f643e8023')


###########################################################################################################
# dmatools
###########################################################################################################
tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='cameradims',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='55aa2dd24828')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='deconrank',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='defa57c7775e')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='dma_filelist_generation',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='6a2bb42acfe4')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='flag_remove_peaks',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='6701ecb1a3b0')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='flag_remove_peaks',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='6701ecb1a3b0')


tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='h_concatenate',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='94b55c6c1ab0')

tcs.install_repository_revision(tool_shed_url='https://testtoolshed.g2.bx.psu.edu',
                                name='topn',
                                owner='tomnl',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='7353968f4980')

###########################################################################################################
# xcms
###########################################################################################################
tool_panel_section = 'xcms'
tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='xcms_xcmsset',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='363cce459fff')

tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='xcms_summary',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='4c757d1ba7b4')

tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='xcms_retcor',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='e4e0254a3c0a')

tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='xcms_group',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='13558e8a4778')

tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='xcms_fillpeaks',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='dcb9041cb9ea')

tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='xcms_merge',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id=tool_panel_section,
                                changeset_revision='3a5204f14fff')

###########################################################################################################
# camera
###########################################################################################################
tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='camera_annotate',
                                owner='lecorguille',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='6139bfcc95cb')

tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='camera_combinexsannos',
                                owner='mmonsoor',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='479a83f62863')


###########################################################################################################
# annotation
###########################################################################################################
tcs.install_repository_revision(tool_shed_url='https://toolshed.g2.bx.psu.edu',
                                name='probmetab',
                                owner='mmonsoor',
                                install_tool_dependencies=True,
                                install_repository_dependencies=True,
                                tool_panel_section_id='metabolomics',
                                changeset_revision='52b222a626b0')
