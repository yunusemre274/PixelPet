import AppKit

/// Renders pixel-art sprite frames with nearest-neighbor scaling.
///
/// Handles:
/// - Crisp pixel art rendering (no bilinear filtering)
/// - Animation frame cycling at configurable FPS
/// - Horizontal flip for direction changes
/// - Click detection on non-transparent pixels
///
/// M3 scope: sprite rendering with animation support.
final class SpriteView: NSView {

    /// The current animation frames to cycle through.
    private(set) var frames: [NSImage] = []

    /// Index of the currently displayed frame.
    private(set) var currentFrameIndex: Int = 0

    /// Whether the sprite is horizontally flipped (facing left).
    var isFacingLeft: Bool = false {
        didSet { needsDisplay = true }
    }

    /// Callback invoked when the sprite is clicked.
    var onClicked: (() -> Void)?

    /// Timer for frame animation.
    private var animationTimer: Timer?

    /// Whether the current animation should loop.
    private var animationLoops: Bool = true

    override init(frame: NSRect) {
        super.init(frame: frame)
        setupLayer()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("Not implemented")
    }

    private func setupLayer() {
        wantsLayer = true
        // Nearest-neighbor filtering for crisp pixel art
        layer?.magnificationFilter = .nearest
        layer?.minificationFilter = .nearest
    }

    // MARK: - Animation Control

    /// Sets the animation frames and starts playback.
    ///
    /// - Parameters:
    ///   - frames: Array of NSImage frames.
    ///   - fps: Frames per second for animation.
    ///   - loop: Whether to loop the animation.
    func setAnimation(frames: [NSImage], fps: Double, loop: Bool = true) {
        stopAnimation()

        self.frames = frames
        self.currentFrameIndex = 0
        self.animationLoops = loop

        needsDisplay = true

        guard frames.count > 1, fps > 0 else { return }

        let interval = 1.0 / fps
        animationTimer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { [weak self] _ in
            self?.advanceFrame()
        }
    }

    /// Stops the current animation.
    func stopAnimation() {
        animationTimer?.invalidate()
        animationTimer = nil
    }

    private func advanceFrame() {
        guard !frames.isEmpty else { return }

        let nextIndex = currentFrameIndex + 1

        if nextIndex >= frames.count {
            if animationLoops {
                currentFrameIndex = 0
            } else {
                // Stay on last frame
                stopAnimation()
                return
            }
        } else {
            currentFrameIndex = nextIndex
        }

        needsDisplay = true
    }

    // MARK: - Drawing

    override func draw(_ dirtyRect: NSRect) {
        guard let ctx = NSGraphicsContext.current?.cgContext else { return }
        guard currentFrameIndex < frames.count else {
            // No frames loaded — clear the view
            ctx.clear(bounds)
            return
        }

        // Clear for transparency
        ctx.clear(bounds)

        // Disable interpolation for crisp pixel art
        ctx.interpolationQuality = .none

        let image = frames[currentFrameIndex]

        // Get the CGImage for drawing
        guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return }

        ctx.saveGState()

        if isFacingLeft {
            // Flip horizontally: translate to right edge, then scale X by -1
            ctx.translateBy(x: bounds.width, y: 0)
            ctx.scaleBy(x: -1, y: 1)
        }

        // Draw the image filling the entire view bounds (scaling happens here)
        ctx.draw(cgImage, in: bounds)

        ctx.restoreGState()
    }

    // MARK: - Click Handling

    override func mouseDown(with event: NSEvent) {
        // Check if the click hit a non-transparent pixel
        let locationInView = convert(event.locationInWindow, from: nil)

        if isOpaquePixel(at: locationInView) {
            onClicked?()
        }
    }

    override func hitTest(_ point: NSPoint) -> NSView? {
        let localPoint = convert(point, from: superview)
        guard bounds.contains(localPoint) else { return nil }

        if isOpaquePixel(at: localPoint) {
            return self
        }
        return nil
    }

    // MARK: - Pixel Hit Testing

    /// Checks if the pixel at the given view-local point is non-transparent.
    private func isOpaquePixel(at point: NSPoint) -> Bool {
        guard currentFrameIndex < frames.count else { return false }

        let image = frames[currentFrameIndex]
        guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return false }

        let imageWidth = cgImage.width
        let imageHeight = cgImage.height

        // Map view coordinates to image pixel coordinates
        var pixelX = Int(point.x / bounds.width * CGFloat(imageWidth))
        let pixelY = imageHeight - 1 - Int(point.y / bounds.height * CGFloat(imageHeight))

        // Account for horizontal flip
        if isFacingLeft {
            pixelX = imageWidth - 1 - pixelX
        }

        guard pixelX >= 0, pixelX < imageWidth, pixelY >= 0, pixelY < imageHeight else { return false }

        // Read the pixel's alpha value
        guard let dataProvider = cgImage.dataProvider,
              let data = dataProvider.data,
              let ptr = CFDataGetBytePtr(data) else { return false }

        let bytesPerPixel = cgImage.bitsPerPixel / 8
        let bytesPerRow = cgImage.bytesPerRow
        let offset = pixelY * bytesPerRow + pixelX * bytesPerPixel

        // Alpha is typically the last component in RGBA
        let alphaIndex = bytesPerPixel - 1
        let alpha = ptr[offset + alphaIndex]

        return alpha > 20  // Small threshold to handle near-transparent edges
    }

    deinit {
        stopAnimation()
    }
}
