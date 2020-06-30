movie:
	ffmpeg -framerate 8 -i images/plot-%3d.png -framerate 8 -i images/image-%3d.png -filter_complex "[0]scale=1280:960[left];[1]scale=1280:960[right];[left][right]hstack=inputs=2" -vcodec libx264 -pix_fmt yuv420p output.mp4
